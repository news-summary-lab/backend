package com.restapi;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
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

    @PostMapping
    public ResponseEntity<Map<String, String>> summarize(@RequestBody Article article) {
        if (article.getText() == null || article.getText().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message", "프롬프트를 입력하세요."));
        }

        String summary = summaryService.summarize(article);
        return ResponseEntity.ok(Map.of("original", article.getText(), "summary", summary));
    }

    @GetMapping("/history")
    public ResponseEntity<List<Conversation>> getHistory() {
        return ResponseEntity.ok(summaryService.getConversationHistory());
    }
}