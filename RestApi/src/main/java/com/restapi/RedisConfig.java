package com.restapi;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;

@Configuration
public class RedisConfig {
	 @Bean
	    public RedisTemplate<String, Conversation> conversationRedisTemplate(RedisConnectionFactory connectionFactory) {
	        RedisTemplate<String, Conversation> template = new RedisTemplate<>();
	        template.setConnectionFactory(connectionFactory);

	        ObjectMapper mapper = new ObjectMapper();
	        mapper.activateDefaultTyping(
	                LaissezFaireSubTypeValidator.instance,
	                ObjectMapper.DefaultTyping.EVERYTHING,
	                JsonTypeInfo.As.PROPERTY
	        );

	        GenericJackson2JsonRedisSerializer serializer = new GenericJackson2JsonRedisSerializer(mapper);
	        template.setKeySerializer(new StringRedisSerializer());
	        template.setValueSerializer(serializer);
	        template.setDefaultSerializer(serializer);

	        template.afterPropertiesSet();
	        return template;
	    }
}
