package com.jobapp.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "upwork_jobs")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpworkJob {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String url;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Builder.Default
    @Column(name = "proposal_created", nullable = false)
    private Boolean proposalCreated = false;

    @Builder.Default
    @Column(name = "cover_letter_created", nullable = false)
    private Boolean coverLetterCreated = false;

    @Column(columnDefinition = "TEXT")
    private String question1;

    @Column(columnDefinition = "TEXT")
    private String question2;

    @Column(columnDefinition = "TEXT")
    private String question3;

    @Column(columnDefinition = "TEXT")
    private String question4;

    @Column(name = "processed_datetime")
    private LocalDateTime processedDatetime;
}
