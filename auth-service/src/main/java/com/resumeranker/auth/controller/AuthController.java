package com.resumeranker.auth.controller;

import com.resumeranker.auth.dto.AuthResponse;
import com.resumeranker.auth.dto.LoginRequest;
import com.resumeranker.auth.dto.RegisterRequest;
import com.resumeranker.auth.dto.TokenValidationResponse;
import com.resumeranker.auth.service.AuthService;
import com.resumeranker.auth.util.JwtUtil;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@CrossOrigin(origins = "*")
public class AuthController {
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(authService.register(request));
    }
    
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }
    
    @PostMapping("/validate")
    public ResponseEntity<TokenValidationResponse> validateToken(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
            
            if (jwtUtil.validateToken(token)) {
                String username = jwtUtil.extractUsername(token);
                String role = jwtUtil.extractClaim(token, claims -> claims.get("role", String.class));
                
                return ResponseEntity.ok(new TokenValidationResponse(true, username, role));
            } else {
                return ResponseEntity.ok(new TokenValidationResponse(false, null, null));
            }
        } catch (Exception e) {
            return ResponseEntity.ok(new TokenValidationResponse(false, null, null));
        }
    }
}

