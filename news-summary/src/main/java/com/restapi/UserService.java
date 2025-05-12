package com.restapi;

import java.util.ArrayList;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService implements UserDetailsService{

	@Autowired
	private UserRepository userRepository;
	
	@Autowired
	private PasswordEncoder passwordEncoder;
	
	public User create(User user) {
		
		user.setPassword(passwordEncoder.encode(user.getPassword()));
		this.userRepository.save(user);
		return user;
	}
	
	 @Override
	 public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
		 User user = userRepository.findByemail(email)
	            .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다."));
	        
	     return new org.springframework.security.core.userdetails.User(
	    		 user.getEmail(),
	             user.getPassword(),
	             new ArrayList<>()
	        );
	    }
	
	public int emailCheck(String email) {
	    return userRepository.findByemail(email).isPresent() ? 1 : 0;
	}
}
