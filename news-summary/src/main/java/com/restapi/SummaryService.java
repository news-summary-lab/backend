package com.restapi;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service 
public class SummaryService { 
	
	private final RestTemplate restTemplate = new RestTemplate();
	private final RedisTemplate<String, Conversation> redisTemplate;
  
	public String summarize(Article article, Integer userId) { 
		String fastApiUrl = "http://localhost:8000/summarize";
		String summary = restTemplate.postForObject(fastApiUrl, article, String.class);
		
		/*
		 * String key = getRedisKey(userId); Conversation conv = new
		 * Conversation(article.getText(), summary);
		 * redisTemplate.opsForList().rightPush(key, conv);
		 */
		
		if (userId != null) {
	        String key = "conversation:user:" + userId;
	        Conversation conv = new Conversation(article.getText(), summary);
	        redisTemplate.opsForList().rightPush(key, conv);
	    }
		
		return summary; 
	  }
	
	public List<Conversation> getConversationHistory(Integer userId) {
		String key = new String();
		if(userId!=null) {
			key="conversation:user:" + userId;
			return redisTemplate.opsForList().range(key, 0, -1);
		}
		else {
			return null;
		}
	}
	
  }
 