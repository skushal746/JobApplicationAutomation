package com.jobapp.service;

import com.jobapp.dto.WorkerStatusResponse;
import com.jobapp.entity.WorkerControl;
import com.jobapp.entity.WorkerState;
import com.jobapp.repository.WorkerControlRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class WorkerControlService {

    /** The worker reports every 10 seconds; allow a few missed beats before calling it offline. */
    private static final Duration ONLINE_WINDOW = Duration.ofSeconds(45);

    private final WorkerControlRepository repository;

    public WorkerStatusResponse getStatus(Long userId) {
        return toResponse(repository.findById(userId).orElseGet(() -> WorkerControl.builder().userId(userId).build()));
    }

    /** "Run now". Repeated clicks keep the first request's time; the worker runs once for them. */
    @Transactional
    public WorkerStatusResponse requestRun(Long userId) {
        WorkerControl control = getOrCreate(userId);
        if (control.getRunRequestedAt() == null) {
            control.setRunRequestedAt(LocalDateTime.now());
        }
        return toResponse(repository.save(control));
    }

    /** Called by the worker every few seconds; the answer tells it whether a run is waiting. */
    @Transactional
    public WorkerStatusResponse heartbeat(Long userId, WorkerState state) {
        WorkerControl control = getOrCreate(userId);
        control.setState(state);
        control.setLastSeenAt(LocalDateTime.now());
        return toResponse(repository.save(control));
    }

    /** True if there was a pending request and this call took it. */
    @Transactional
    public boolean claimRun(Long userId) {
        return repository.claimRunRequest(userId) == 1;
    }

    // If two first-ever requests race, one insert fails and that request errors once;
    // the worker retries on its next heartbeat and the UI on its next click.
    private WorkerControl getOrCreate(Long userId) {
        return repository.findById(userId)
                .orElseGet(() -> repository.saveAndFlush(WorkerControl.builder().userId(userId).build()));
    }

    private WorkerStatusResponse toResponse(WorkerControl control) {
        LocalDateTime lastSeen = control.getLastSeenAt();
        boolean online = lastSeen != null
                && control.getState() != WorkerState.STOPPED
                && lastSeen.isAfter(LocalDateTime.now().minus(ONLINE_WINDOW));
        return new WorkerStatusResponse(
                control.getRunRequestedAt() != null,
                control.getRunRequestedAt(),
                control.getState(),
                lastSeen,
                online
        );
    }
}
