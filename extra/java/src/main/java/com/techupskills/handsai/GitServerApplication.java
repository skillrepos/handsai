package com.techupskills.handsai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Lab 6's wrapped git server, in Spring Boot.
 *
 * A battle-tested CLI on the inside, a typed and governed MCP boundary on the
 * outside. Annotated tool beans are discovered and published automatically.
 */
@SpringBootApplication
public class GitServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(GitServerApplication.class, args);
    }
}
