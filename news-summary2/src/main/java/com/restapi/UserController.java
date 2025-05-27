package com.restapi;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

import lombok.RequiredArgsConstructor;

@Controller
@RequiredArgsConstructor
@CrossOrigin("*")
public class UserController {

private final UserService userService;
	
	//로그인 화면 출력
	@GetMapping("/login_signin")
	public String goLogin() {
		return "login_signin";
	}
		
	@PostMapping("/sign_up")
	public String signUp(User user) {
		System.out.println(user.getName());
		System.out.println(user.getEmail());

		if(userService.emailCheck(user.getEmail()) == 0) {
			userService.create(user);
			return "signUpSuccess";
		}
		else
			return "signUpFail";
	}
	
	@GetMapping("/logout")
	public String logout() {
		return "logout";
	}
}
