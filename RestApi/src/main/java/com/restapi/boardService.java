package com.restapi;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class boardService {

	private final boardRepository boardrepository;
	
	public board getBoardById(Integer id) {
		return this.boardrepository.findById(id)
				 .orElseThrow(() -> new RuntimeException("게시글을 찾을 수 없습니다."));
	}
	
	@Transactional
	public void postBoard(board board) {
		this.boardrepository.save(board);
	}
	
	@Transactional
	public void putBoard(Integer id, board board) {
		board b=this.boardrepository.findById(id).orElseThrow(() -> new RuntimeException("게시글을 찾을 수 없습니다."));
		this.boardrepository.updateBoard(id,board.getContent());
	}
}
