package com.restapi;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;


  @Service public class SummaryService { 
	  private final RestTemplate restTemplate = new RestTemplate();
  
	  public String summarize(Article article) { 
		  String fastApiUrl = "http://localhost:8000/summarize"; 
		  return restTemplate.postForObject(fastApiUrl, article, String.class); 
	  } 
  }
 