package com.jobapp.repository;

import com.jobapp.entity.WorkerControl;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface WorkerControlRepository extends JpaRepository<WorkerControl, Long> {

    /**
     * Clears a pending run request in a single statement and returns 1 if there was one.
     * Being one UPDATE, two claims can never both succeed for the same request.
     */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("update WorkerControl w set w.runRequestedAt = null where w.userId = :userId and w.runRequestedAt is not null")
    int claimRunRequest(@Param("userId") Long userId);
}
