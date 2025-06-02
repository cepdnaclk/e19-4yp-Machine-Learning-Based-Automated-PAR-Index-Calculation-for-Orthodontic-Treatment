package com.orthodontics.filemanagement.repository;

import com.orthodontics.filemanagement.model.STLFiles;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface STLFileRepository extends JpaRepository<STLFiles, Long> {
    @Query("SELECT s FROM STLFiles s WHERE s.patient_id = ?1")
    STLFiles findByPatient_id(Long patientId);
}
    /**
     * This method takes a patientId as a parameter and returns an STLFiles object which matches the given patientId.
     * The @Query annotation is used to specify a custom query to be executed.
     * The query is in HQL (Hibernate Query Language) which is similar to SQL.
     * The parameter ?1 is used to specify the parameter which is passed to the method.
     * The parameter is used in the WHERE clause to filter the results.
     * The result is a single STLFiles object which is the one that matches the given patientId.
     */
