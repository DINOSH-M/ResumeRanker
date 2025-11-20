package com.resumeranker.resumeclient.controller;

import com.resumeranker.resumeclient.dto.RankResponse;
import com.resumeranker.resumeclient.dto.TokenValidationResponse;
import com.resumeranker.resumeclient.service.AuthValidationService;
import com.resumeranker.resumeclient.service.ResumeRankerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.multipart.FilePart;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/resume")
@CrossOrigin(origins = "*")
public class ResumeController {
    
    @Autowired
    private ResumeRankerService resumeRankerService;
    
    @Autowired
    private AuthValidationService authValidationService;
    
    @PostMapping(value = "/rank", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Mono<ResponseEntity<?>> rankResume(
            @RequestHeader(HttpHeaders.AUTHORIZATION) String authHeader,
            @RequestPart("resume") FilePart resume,
            @RequestPart("job_description") FilePart jobDescription) {
        
        String token = authHeader.startsWith("Bearer ") ? authHeader.substring(7) : authHeader;
        
        return authValidationService.validateTokenWithDetails(token)
                .flatMap(validationResponse -> {
                    if (!validationResponse.isValid()) {
                        return Mono.<ResponseEntity<?>>just(ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                                .body("Invalid or expired token"));
                    }
                    
                    return resumeRankerService.rankResume(resume, jobDescription)
                            .<ResponseEntity<?>>map(ResponseEntity::ok)
                            .onErrorResume(e -> Mono.<ResponseEntity<?>>just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                                    .body("Error ranking resume: " + e.getMessage())));
                });
    }
    
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Resume Client Service is healthy");
    }
}

