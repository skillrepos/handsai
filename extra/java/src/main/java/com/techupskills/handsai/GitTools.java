package com.techupskills.handsai;

import java.time.Duration;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.stereotype.Service;

/**
 * The Java twin of mcptools/git_server.py.
 *
 * Same three rules as the Python version:
 *   1. allowlist first - policy is one reviewable line, not emergent behavior
 *   2. fixed argument list - no shell string for a model to inject into
 *   3. errors come back as DATA, so the model can read them and adapt
 */
@Service
public class GitTools {

    /** Policy lives here. This is the line your security reviewer reads. */
    private static final Set<String> ALLOWED_SUBCOMMANDS =
            Set.of("status", "log", "diff", "branch", "show");

    private static final Duration TIMEOUT = Duration.ofSeconds(10);

    @McpTool(description = """
            Run a read-only git subcommand (status, log, diff, branch, show)
            with optional arguments and get structured output back.""")
    public GitResult gitCommand(
            @McpToolParam(description = "The git subcommand, e.g. 'log'") String subcommand,
            @McpToolParam(description = "Optional arguments, e.g. ['-3', '--oneline']", required = false)
            List<String> args) {
        return runGit(subcommand, args == null ? List.of() : args);
    }

    @McpTool(description = """
            Summarize how many files changed and how many lines were
            added or removed in the working tree.""")
    public GitResult diffSummary() {
        return runGit("diff", List.of("--shortstat"));
    }

    // ---------------------------------------------------------------
    // The wrap boundary: validate, then execute with a fixed argv.
    // ---------------------------------------------------------------
    private GitResult runGit(String subcommand, List<String> args) {
        if (!ALLOWED_SUBCOMMANDS.contains(subcommand)) {
            return GitResult.denied(
                    "subcommand '" + subcommand + "' is not allowed",
                    ALLOWED_SUBCOMMANDS.stream().sorted().toList());
        }

        try {
            var command = new java.util.ArrayList<String>();
            command.add("git");
            command.add(subcommand);
            command.addAll(args);

            // ProcessBuilder takes a list, not a string - nothing to inject into.
            Process process = new ProcessBuilder(command)
                    .redirectErrorStream(false)
                    .start();

            if (!process.waitFor(TIMEOUT.toSeconds(), TimeUnit.SECONDS)) {
                process.destroyForcibly();
                return GitResult.denied("git command timed out", List.of());
            }

            String stdout = new String(process.getInputStream().readAllBytes());
            String stderr = new String(process.getErrorStream().readAllBytes());

            if (process.exitValue() != 0) {
                return GitResult.denied(truncate(stderr, 500), List.of());
            }
            return GitResult.ok(truncate(stdout, 2000));

        } catch (Exception e) {
            // Errors as data: the model reads this and tries something allowed.
            return GitResult.denied(e.getMessage(), List.of());
        }
    }

    private static String truncate(String s, int max) {
        return s.length() <= max ? s : s.substring(0, max);
    }

    /**
     * Structured output the model cannot misread - the Java equivalent of
     * returning json.dumps({...}) from the Python tool.
     */
    public record GitResult(String output, String error, List<String> allowed) {
        static GitResult ok(String output) {
            return new GitResult(output, null, null);
        }
        static GitResult denied(String error, List<String> allowed) {
            return new GitResult(null, error, allowed.isEmpty() ? null : allowed);
        }
    }
}

/*
 * ---------------------------------------------------------------------------
 * Spring AI 1.x shape, for reference
 * ---------------------------------------------------------------------------
 * In Spring AI 1.x the annotation is @Tool (org.springframework.ai.tool.annotation)
 * and tools are registered explicitly:
 *
 *   @Tool(description = "Run a read-only git subcommand ...")
 *   public GitResult gitCommand(String subcommand, List<String> args) { ... }
 *
 *   @Bean
 *   ToolCallbackProvider gitToolCallbacks(GitTools gitTools) {
 *       return MethodToolCallbackProvider.builder().toolObjects(gitTools).build();
 *   }
 *
 * Same method body, same allowlist, same structured return. Check which Spring AI
 * version your organization is on - see README.md.
 */
