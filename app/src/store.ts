import { configureStore } from '@reduxjs/toolkit';
import baseApi from './api';

declare global {
	type RootState = ReturnType<typeof store.getState>;
}

export const store = configureStore({
	reducer: {
		[baseApi.reducerPath]: baseApi.reducer,
	},
	middleware: (getDefaultMiddleware) =>
		getDefaultMiddleware({
			serializableCheck: false,
		}).concat(baseApi.middleware),
});
