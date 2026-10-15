package com.jobapp.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "job_entry",
        uniqueConstraints = @UniqueConstraint(
                name = "uk_job_entry_user_url",
                columnNames = {"user_id", "url"}
        )
)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class JobEntry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Plain id rather than a @ManyToOne to User, so serializing a JobEntry
    // never pulls in the user's password hash. The foreign key lives in the database.
    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false, length = 700)
    private String url;

    // Enums are stored by name in VARCHAR columns. The JdbcTypeCode stops Hibernate
    // from expecting a native MySQL ENUM column during schema validation.
    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "job_type", nullable = false, length = 50)
    private JobType jobType;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 30)
    private JobEntryStatus status = JobEntryStatus.PENDING;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // Null until the entry is first modified. Hibernate's @UpdateTimestamp would also
    // fill it on insert, so it is set here only on updates.
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PreUpdate
    void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
