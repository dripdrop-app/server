import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export const youtubeSlice = createSlice({
	name: 'youtube',
	initialState: {
		queue: {
			player: null as Record<string, any> | null,
			video: null as YoutubeVideo | null,
			index: 1,
			playing: false,
			ended: false,
			duration: 0,
			progress: 0,
			hide: false,
		},
	},
	reducers: {
		setVideoQueuePlayer: (state, action: PayloadAction<Record<string, any>>) => {
			const player = action.payload;
			if (player) {
				if (state.queue.playing && state.queue.video) {
					player.loadVideoById(state.queue.video.id, 0);
				}
			}
			state.queue.player = player;
		},
		setVideoQueuePlayerVideo: (state, action: PayloadAction<YoutubeVideo>) => {
			state.queue.video = action.payload;
			state.queue.ended = false;
			state.queue.progress = 0;
			state.queue.duration = 0;
		},
		advanceVideoQueue: (state) => {
			state.queue.index++;
		},
		reverseVideoQueue: (state) => {
			state.queue.index--;
		},
		setVideoQueueIndex: (state, action: PayloadAction<number>) => {
			state.queue.index = action.payload;
		},
		playVideoQueue: (state) => {
			if (state.queue.player) {
				const player = state.queue.player;
				const playerState = player.getPlayerState();
				if (playerState !== 1) {
					player.playVideo();
					state.queue.playing = true;
				}
			}
		},
		pauseVideoQueue: (state) => {
			if (state.queue.player) {
				const player = state.queue.player;
				const playerState = player.getPlayerState();
				if (playerState !== 2) {
					player.pauseVideo();
					state.queue.playing = false;
				}
			}
		},
		endVideoQueue: (state) => {
			state.queue.ended = true;
		},
		updateVideoQueueProgress: (state, action: PayloadAction<number>) => {
			state.queue.progress = action.payload;
		},
		updateVideoQueueDuration: (state, action: PayloadAction<number>) => {
			state.queue.duration = action.payload;
		},
		hideVideoQueueDisplay: (state) => {
			state.queue.hide = true;
		},
		showVideoQueueDisplay: (state) => {
			state.queue.hide = false;
		},
	},
});

export const {
	setVideoQueuePlayer,
	setVideoQueuePlayerVideo,
	pauseVideoQueue,
	playVideoQueue,
	endVideoQueue,
	updateVideoQueueDuration,
	updateVideoQueueProgress,
	hideVideoQueueDisplay,
	showVideoQueueDisplay,
	advanceVideoQueue,
	reverseVideoQueue,
	setVideoQueueIndex,
} = youtubeSlice.actions;
