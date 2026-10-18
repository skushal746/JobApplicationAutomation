package com.jobapp.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "worker_control")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WorkerControl {

    @Id
    @Column(name = "user_id")
    private Long userId;

    /** Set by "Run now"; cleared when the worker claims it. */
    @Column(name = "run_requested_at")
    private LocalDateTime runRequestedAt;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 20)
    private WorkerState state;

    @Column(name = "last_seen_at")
    private LocalDateTime lastSeenAt;
}
