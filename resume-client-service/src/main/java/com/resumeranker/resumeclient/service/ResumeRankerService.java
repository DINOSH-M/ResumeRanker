package com.resumeranker.resumeclient.service;

import com.resumeranker.resumeclient.dto.RankResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferUtils;
import org.springframework.http.MediaType;
import org.springframework.http.codec.multipart.FilePart;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class ResumeRankerService {
    
    private final WebClient webClient;
    
    public ResumeRankerService(@Value("${resume-ranker.service.url}") String rankerServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(rankerServiceUrl)
                .build();
    }
    
    public Mono<RankResponse> rankResume(FilePart resume, FilePart jobDescription) {
        return Mono.zip(
                readFilePart(resume),
                readFilePart(jobDescription)
        ).flatMap(tuple -> {
            byte[] resumeBytes = tuple.getT1();
            byte[] jdBytes = tuple.getT2();
            
            // Create multipart parts with proper Content-Type
            MultiValueMap<String, Object> parts = new LinkedMultiValueMap<>();
            
            // Resume file part
            ByteArrayResource resumeResource = new ByteArrayResource(resumeBytes) {
                @Override
                public String getFilename() {
                    return resume.filename() != null ? resume.filename() : "resume.pdf";
                }
            };
            parts.add("resume", resumeResource);
            
            // Job description file part
            ByteArrayResource jdResource = new ByteArrayResource(jdBytes) {
                @Override
                public String getFilename() {
                    return jobDescription.filename() != null ? jobDescription.filename() : "job_description.pdf";
                }
            };
            parts.add("job_description", jdResource);
            
            return webClient.post()
                    .uri("/rank")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(parts))
                    .retrieve()
                    .onStatus(status -> status.is4xxClientError() || status.is5xxServerError(), 
                            response -> response.bodyToMono(String.class)
                                    .flatMap(errorBody -> {
                                        return Mono.error(new RuntimeException("Error from resume-ranker-service: " + 
                                                response.statusCode() + " - " + errorBody));
                                    }))
                    .bodyToMono(RankResponse.class);
        });
    }
    
    private Mono<byte[]> readFilePart(FilePart filePart) {
        return DataBufferUtils.join(filePart.content())
                .map(dataBuffer -> {
                    byte[] bytes = new byte[dataBuffer.readableByteCount()];
                    dataBuffer.read(bytes);
                    DataBufferUtils.release(dataBuffer);
                    return bytes;
                });
    }
}

