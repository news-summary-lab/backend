package com.restapi;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ViewController {
    @GetMapping("/summarize")
    public String index() {
        return "summarize";  // Thymeleaf 템플릿 반환
    }
}
