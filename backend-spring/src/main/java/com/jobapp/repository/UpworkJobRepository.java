package com.jobapp.repository;

import com.jobapp.entity.UpworkJob;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UpworkJobRepository extends JpaRepository<UpworkJob, Long> {
}
