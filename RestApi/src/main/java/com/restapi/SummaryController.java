package com.restapi;


  import java.util.HashMap; import java.util.Map;
  
  import org.springframework.beans.factory.annotation.Autowired; 
  import org.springframework.http.ResponseEntity; 
  import org.springframework.web.bind.annotation.PostMapping; 
  import org.springframework.web.bind.annotation.RequestBody; 
  import org.springframework.web.bind.annotation.RequestMapping; 
  import org.springframework.web.bind.annotation.RestController;
  
  @RestController
  @RequestMapping("/api/summaries") 
  public class SummaryController {
  
	  @Autowired private SummaryService summaryService;
	  
	  @PostMapping 
	  public ResponseEntity<Map<String, String>>summarize(@RequestBody Article article) { 
		  if (article.getText() == null || article.getText().isEmpty()) {
		        Map<String, String> errorResponse = new HashMap<>();
		        errorResponse.put("프롬프트를 입력하세요", "error");
		        return ResponseEntity.badRequest().body(errorResponse);  // 400 Bad Request 반환
		   }
		  String summary = summaryService.summarize(article);
		  
		  System.out.println(article.getText());
		  
		  Map<String, String> response = new HashMap<>(); response.put("original",
		  article.getText()); response.put("summary", summary);
		  
		  return ResponseEntity.ok(response); 
	  } 
  
  }
 