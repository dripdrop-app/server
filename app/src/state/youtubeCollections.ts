import { createSlice, PayloadAction } from '@reduxjs/toolkit';

const initialState = {
	videos: [] as YoutubeVideo[],
	currentIndex: 0,
	currentVideo: undefined as YoutubeVideo | undefined,
};

const getState = () => {
	const videoQueueData = window.localStorage.getItem('videoQueue');
	if (videoQueueData) {
		const videoQueue = JSON.parse(videoQueueData);
		if (!videoQueue.videos[videoQueue.currentIndex]) {
			videoQueue.currentIndex = 0;
			videoQueue.currentVideo = videoQueue.videos[0];
		}
		return videoQueue as typeof initialState;
	}
	return initialState;
};

export const videoQueueSlice = createSlice({
	name: 'videoQueue',
	initialState: getState(),
	reducers: {
		addVideoToQueue: (state, action: PayloadAction<YoutubeVideo>) => {
			state.videos.push(action.payload);
			if (!state.currentVideo) {
				state.currentVideo = state.videos[0];
			}
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		addManyVideosToQueue: (state, action: PayloadAction<YoutubeVideo[]>) => {
			state.videos.push(...action.payload);
			if (!state.currentVideo) {
				state.currentVideo = state.videos[0];
			}
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		removeVideoFromQueue: (state, action: PayloadAction<string>) => {
			const videoIndex = state.videos.findIndex((video) => video.id === action.payload);
			if (videoIndex !== -1) {
				if (videoIndex <= state.currentIndex) {
					state.currentIndex = Math.max(state.currentIndex - 1, 0);
				}
				state.videos.splice(videoIndex, 1);
				state.currentVideo = state.videos[state.currentIndex];
			}
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		moveToIndex: (state, action: PayloadAction<number>) => {
			if (state.videos[action.payload]) {
				state.currentIndex = action.payload;
				state.currentVideo = state.videos[state.currentIndex];
			}
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		advanceQueue: (state) => {
			state.currentIndex = Math.min(state.videos.length - 1, state.currentIndex + 1);
			state.currentVideo = state.videos[state.currentIndex];
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		reverseQueue: (state) => {
			state.currentIndex = Math.max(state.currentIndex - 1, 0);
			state.currentVideo = state.videos[state.currentIndex];
			window.localStorage.setItem('videoQueue', JSON.stringify(state));
		},
		clearQueue: (state) => {
			window.localStorage.setItem('videoQueue', JSON.stringify({ ...initialState }));
			return { ...initialState };
		},
	},
});

export const {
	addVideoToQueue,
	removeVideoFromQueue,
	advanceQueue,
	reverseQueue,
	clearQueue,
	moveToIndex,
	addManyVideosToQueue,
} = videoQueueSlice.actions;
