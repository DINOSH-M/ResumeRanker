package com.resumeranker.apigateway.filter;

import com.resumeranker.apigateway.dto.TokenValidationResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

@Component
public class JwtAuthenticationFilter implements GlobalFilter, Ordered {
    
    private final WebClient webClient;
    private static final List<String> EXCLUDED_PATHS = Arrays.asList("/auth/register", "/auth/login", "/auth/validate", "/actuator");
    
    public JwtAuthenticationFilter(@Value("${auth.service.url}") String authServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(authServiceUrl)
                .build();
    }
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();
        
        // Skip authentication for excluded paths
        if (EXCLUDED_PATHS.stream().anyMatch(path::startsWith)) {
            return chain.filter(exchange);
        }
        
        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return onError(exchange, "Missing or invalid authorization header", HttpStatus.UNAUTHORIZED);
        }
        
        String token = authHeader.substring(7);
        
        return webClient.post()
                .uri("/auth/validate")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                .retrieve()
                .bodyToMono(TokenValidationResponse.class)
                .flatMap(validationResponse -> {
                    if (!validationResponse.isValid()) {
                        return onError(exchange, "Invalid or expired token", HttpStatus.UNAUTHORIZED);
                    }
                    
                    // Add user info to headers for downstream services
                    // Preserve the Authorization header and Content-Type for downstream services
                    ServerHttpRequest.Builder requestBuilder = request.mutate()
                            .header("X-User-Email", validationResponse.getUsername())
                            .header("X-User-Role", validationResponse.getRole())
                            .header(HttpHeaders.AUTHORIZATION, authHeader);  // Preserve original Authorization header
                    
                    // Preserve Content-Type header for multipart requests
                    String contentType = request.getHeaders().getFirst(HttpHeaders.CONTENT_TYPE);
                    if (contentType != null && contentType.contains("multipart")) {
                        requestBuilder.header(HttpHeaders.CONTENT_TYPE, contentType);
                    }
                    
                    return chain.filter(exchange.mutate().request(requestBuilder.build()).build());
                })
                .onErrorResume(e -> onError(exchange, "Authentication failed", HttpStatus.UNAUTHORIZED));
    }
    
    private Mono<Void> onError(ServerWebExchange exchange, String message, HttpStatus status) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(status);
        response.getHeaders().add(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
        DataBuffer buffer = response.bufferFactory().wrap(
                ("{\"error\":\"" + message + "\"}").getBytes(StandardCharsets.UTF_8));
        return response.writeWith(Mono.just(buffer));
    }
    
    @Override
    public int getOrder() {
        return -100;
    }
}

