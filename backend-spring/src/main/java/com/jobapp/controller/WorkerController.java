package com.jobapp.controller;

import com.jobapp.dto.WorkerHeartbeatRequest;
import com.jobapp.dto.WorkerStatusResponse;
import com.jobapp.entity.User;
import com.jobapp.service.WorkerControlService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Coordination between the UI and the worker running on the user's machine.
 * The backend never calls the worker; the worker polls these endpoints.
 */
@RestController
@RequestMapping("/api/worker")
@RequiredArgsConstructor
public class WorkerController {

    private final WorkerControlService workerControlService;

    /** UI: is the worker online, running, or is a run already requested? */
    @GetMapping("/status")
    public ResponseEntity<WorkerStatusResponse> status(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(workerControlService.getStatus(user.getId()));
    }

    /** UI "Run now": ask the worker to process pending entries as soon as it can. */
    @PostMapping("/run")
    public ResponseEntity<WorkerStatusResponse> requestRun(@AuthenticationPrincipal User user) {
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(workerControlService.requestRun(user.getId()));
    }

    /** Worker: report state; the response says whether a run is waiting. */
    @PostMapping("/heartbeat")
    public ResponseEntity<WorkerStatusResponse> heartbeat(@AuthenticationPrincipal User user,
                                                          @Valid @RequestBody WorkerHeartbeatRequest request) {
        return ResponseEntity.ok(workerControlService.heartbeat(user.getId(), request.state()));
    }

    /** Worker: take the pending run request, if there still is one. */
    @PostMapping("/run/claim")
    public ResponseEntity<Map<String, Boolean>> claim(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(Map.of("claimed", workerControlService.claimRun(user.getId())));
    }
}
