package com.jobapp.controller;

import com.jobapp.entity.UpworkJob;
import com.jobapp.service.UpworkJobService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/upwork-jobs")
@RequiredArgsConstructor
public class UpworkJobController {

    private final UpworkJobService upworkJobService;

    @GetMapping
    public ResponseEntity<List<UpworkJob>> getAll() {
        return ResponseEntity.ok(upworkJobService.getAll());
    }

    @PostMapping
    public ResponseEntity<UpworkJob> create(@RequestBody UpworkJob job) {
        return ResponseEntity.ok(upworkJobService.create(job));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (id == null) return ResponseEntity.badRequest().build();
        upworkJobService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
