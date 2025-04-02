package com.restapi;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class indexController {

	@GetMapping("/")
	public String index() {
		return "1";
	}
	
	@GetMapping("/2")
	public String index2() {
		return "2";
	}
	
	@GetMapping("/3")
	public String index3() {
		return "3";
	}
	
	@GetMapping("/4")
	public String index4() {
		return "4";
	}
	
	@GetMapping("/5")
	public String index5() {
		return "5";
	}
	
	@GetMapping("/6")
	public String index6() {
		return "6";
	}
	
	@GetMapping("/7")
	public String index7() {
		return "7";
	}
	
	@GetMapping("/8")
	public String index8() {
		return "8";
	}
	
	@GetMapping("/9")
	public String index9() {
		return "9";
	}
}
