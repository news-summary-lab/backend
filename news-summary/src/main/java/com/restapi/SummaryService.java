package com.restapi;

import java.util.List;
import java.util.Set;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service 
public class SummaryService { 
	
	private final RestTemplate restTemplate = new RestTemplate();
	private final RedisTemplate<String, Conversation> redisTemplate;
	private final ConversationHistoryRepository conversationHistoryRepository;
  
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
	
	public void migrateConversationsToDatabase() {
	    Set<String> keys = redisTemplate.keys("conversation:user:*");

	    if (keys == null) return;

	    for (String key : keys) {
	        List<Conversation> conversations = redisTemplate.opsForList().range(key, 0, -1);
	        if (conversations != null && !conversations.isEmpty()) {
	        	String userIdStr=key.replace("conversation:user:", "");
	        	Integer userId=Integer.parseInt(userIdStr);
	        	
	        	List<ConversationHistory> historyList = conversations.stream().map(conv -> {
	                ConversationHistory history = new ConversationHistory();
	                history.setPrompt(conv.getPrompt());
	                history.setResponse(conv.getResponse());

	                User user = new User();
	                user.setId(userId);
	                history.setUser(user);

	                return history;
	            }).toList();

	            
	            this.conversationHistoryRepository.saveAll(historyList);

	            
	            redisTemplate.delete(key);
	            System.out.println("✅ Migrated and deleted: " + key);
	        }
	    }
	}

	public List<ConversationHistory> getConversationHistoryFromDatabase(Integer userId) {
		return conversationHistoryRepository.findByUserIdOrderByIdAsc(userId);
	}
	
	
  }
 