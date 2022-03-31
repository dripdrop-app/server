import { configureStore } from '@reduxjs/toolkit';
import baseApi from './api';
import { musicSlice } from './state/music';
import { videoQueueSlice } from './state/youtubeCollections';

declare global {
	type RootState = ReturnType<typeof store.getState>;
}

export const store = configureStore({
	reducer: {
		[baseApi.reducerPath]: baseApi.reducer,
		[musicSlice.name]: musicSlice.reducer,
		[videoQueueSlice.name]: videoQueueSlice.reducer,
	},
	middleware: (getDefaultMiddleware) =>
		getDefaultMiddleware({
			serializableCheck: false,
		}).concat(baseApi.middleware),
});
