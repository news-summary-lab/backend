package com.restapi;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ConversationHistoryRepository extends JpaRepository<ConversationHistory,Integer>{
	
	List<ConversationHistory> findByUserIdOrderByIdAsc(Integer userId);

}
