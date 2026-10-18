package com.jobapp.dto;

import com.jobapp.entity.WorkerState;
import jakarta.validation.constraints.NotNull;

public record WorkerHeartbeatRequest(@NotNull WorkerState state) {
}
