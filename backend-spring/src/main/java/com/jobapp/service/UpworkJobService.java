package com.jobapp.service;

import com.jobapp.entity.UpworkJob;
import com.jobapp.repository.UpworkJobRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UpworkJobService {

    private final UpworkJobRepository upworkJobRepository;

    public List<UpworkJob> getAll() {
        return upworkJobRepository.findAll();
    }

    public UpworkJob create(UpworkJob job) {
        job.setId(null);
        job.setProcessedDatetime(null);
        return upworkJobRepository.save(job);
    }

    public void delete(Long id) {
        if (id == null) throw new IllegalArgumentException("Job id must not be null");
        upworkJobRepository.deleteById(id);
    }
}
