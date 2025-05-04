package com.restapi;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

public interface boardRepository extends JpaRepository<board,Integer>{
	
	Optional<board> findById(Integer id);
	
	@Modifying
	@Query("update board b set b.content = :content where b.id = :id")
	void updateBoard(@Param("id") Integer id, @Param("content") String content);
}
