package com.example.demo.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Set;

@Component
public class DemoWriteProtectionFilter extends OncePerRequestFilter {

    private static final String WRITE_TOKEN_HEADER = "X-Demo-Write-Token";
    private static final Set<String> WRITE_METHODS = Set.of("POST", "PUT", "PATCH", "DELETE");
    private static final Set<String> ALLOWED_ORIGINS = Set.of(
            "http://localhost:5173",
            "https://woongpro416.github.io"
    );

    @Value("${app.demo.write-protection-enabled:true}")
    private boolean writeProtectionEnabled;

    @Value("${app.demo.write-token:}")
    private String writeToken;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        if (!requiresWriteProtection(request) || hasWriteAccess(request)) {
            filterChain.doFilter(request, response);
            return;
        }

        rejectWriteRequest(request, response);
    }

    private boolean requiresWriteProtection(HttpServletRequest request) {
        return writeProtectionEnabled
                && request.getRequestURI().startsWith("/api")
                && WRITE_METHODS.contains(request.getMethod());
    }

    private boolean hasWriteAccess(HttpServletRequest request) {
        if (writeToken == null || writeToken.isBlank()) {
            return false;
        }

        String requestToken = request.getHeader(WRITE_TOKEN_HEADER);
        return writeToken.equals(requestToken);
    }

    private void rejectWriteRequest(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String origin = request.getHeader(HttpHeaders.ORIGIN);
        if (ALLOWED_ORIGINS.contains(origin)) {
            response.setHeader(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, origin);
            response.setHeader(HttpHeaders.VARY, HttpHeaders.ORIGIN);
        }

        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{"
                + "\"status\":403,"
                + "\"error\":\"Forbidden\","
                + "\"message\":\"Demo write access is disabled. Read-only API requests are allowed.\""
                + "}");
    }
}
