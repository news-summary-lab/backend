package com.restapi;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@RestController
@RequestMapping("/board")
public class boardController {

	private final boardService boardservice;
	
	@GetMapping("/{id}")
	public ResponseEntity<board> getBoardById(@PathVariable("id") int id) {
		board board=this.boardservice.getBoardById(id);
		return ResponseEntity.ok(board);
	}
	
	@PostMapping
	public ResponseEntity<String> postBoard(@RequestBody board board){
		this.boardservice.postBoard(board);
		return ResponseEntity.ok("학과가 추가되었습니다.");
	}
	
	@PutMapping("/{id}")
	public ResponseEntity<String> putBoard(@PathVariable("id") int id,@RequestBody board board){
		this.boardservice.putBoard(id,board);
		return ResponseEntity.ok("수정 완료");
	}
}
