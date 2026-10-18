package com.jobapp.dto;

import com.jobapp.entity.WorkerState;

import java.time.LocalDateTime;

/**
 * @param online true when the worker reported in recently and has not said it stopped.
 *               Worked out on the server so the browser's clock and time zone don't matter.
 */
public record WorkerStatusResponse(
        boolean runRequested,
        LocalDateTime runRequestedAt,
        WorkerState state,
        LocalDateTime lastSeenAt,
        boolean online
) {
}
