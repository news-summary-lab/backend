package com.restapi;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/summaries")
public class SummaryController {

    @Autowired 
    private SummaryService summaryService;
    
    @Autowired
    private UserService userService;

    @PostMapping
    public ResponseEntity<Map<String, String>> summarize(@RequestBody Article article) {
    	User user = this.userService.authen();
        Integer userid = (user != null) ? user.getId() : null;
        
        if (article.getText() == null || article.getText().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message", "프롬프트를 입력하세요."));
        }
        
        String summary = summaryService.summarize(article, userid);
        return ResponseEntity.ok(Map.of("original", article.getText(), "summary", summary));
    }

    @GetMapping("/history")
    public ResponseEntity<List<Conversation>> getHistory() {
    	User user = this.userService.authen();
        Integer userid = (user != null) ? user.getId() : null;
        
        return ResponseEntity.ok(summaryService.getConversationHistory(userid));
    }
    
    @PreAuthorize("!authentication.principal.equals('anonymousUser')")
    @GetMapping("/userinfo")
    public ResponseEntity<?> getUserInfo() {
        User user = userService.authen();
        System.out.println(user);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "guest"));
        }

        return ResponseEntity.ok(Map.of(
            "id", user.getId(),
            "email", user.getEmail(),
            "name", user.getName()
        ));
    }
}