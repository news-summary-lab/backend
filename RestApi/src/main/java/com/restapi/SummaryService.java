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
  
	public String summarize(Article article) { 
		String fastApiUrl = "http://localhost:8000/summarize";
		String summary = restTemplate.postForObject(fastApiUrl, article, String.class);
		Conversation conv = new Conversation(article.getText(), summary);
        redisTemplate.opsForList().rightPush("conversation", conv);
		
		return summary; 
	  }
	
	public List<Conversation> getConversationHistory() {
	    return redisTemplate.opsForList().range("conversation", 0, -1);
	}
  }
 