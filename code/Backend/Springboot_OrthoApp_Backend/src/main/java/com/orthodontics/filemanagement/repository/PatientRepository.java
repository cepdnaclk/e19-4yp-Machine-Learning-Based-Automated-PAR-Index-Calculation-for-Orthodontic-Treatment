package com.orthodontics.filemanagement.repository;

import com.orthodontics.filemanagement.model.Patient;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PatientRepository  extends JpaRepository<Patient, Long> {

    List<Patient> findByName(String name);
}
