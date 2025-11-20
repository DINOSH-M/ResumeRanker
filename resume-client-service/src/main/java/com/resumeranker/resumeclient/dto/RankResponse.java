package com.resumeranker.resumeclient.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RankResponse {
    @JsonProperty("similarity_score")
    private Double similarityScore;
    
    @JsonProperty("llm_analysis")
    private String llmAnalysis;
}

