package com.restapi;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class RedisBackupScheduler {

	private final SummaryService summaryService;
	
	/* @Scheduled(fixedRate = 1000 * 60 * 60 * 48) */
	@Scheduled(fixedRate = 1000 * 60)
	public void backupRedisData() {
		/* summaryService.migrateConversationsToDatabase(); */
	}
}
