import { BaseQueryApi } from '@reduxjs/toolkit/dist/query/baseQueryTypes';
import { FetchBaseQueryArgs } from '@reduxjs/toolkit/dist/query/fetchBaseQuery';
import { createApi, fetchBaseQuery, FetchArgs } from '@reduxjs/toolkit/query/react';

export const errorParser = (error: ErrorResponse | undefined) => {
	if (error && typeof error.detail === 'string') {
		return error.detail;
	} else if (error && typeof error.detail !== 'string') {
		return error.detail.reduce((msg, error) => {
			const field = error.loc.pop();
			if (field) {
				let message = error.msg.replace('value', field);
				message = message.charAt(0).toLocaleUpperCase() + message.substring(1);
				msg = !msg ? message : `${msg}, ${message}`;
			}
			return msg;
		}, '');
	}
	return error;
};

const customBaseQuery = (options?: FetchBaseQueryArgs) => {
	const fetch = fetchBaseQuery(options);
	return async (args: string | FetchArgs, api: BaseQueryApi, extraOptions: {}) => {
		const response = await fetch(args, api, extraOptions);
		let error;
		if (response.error && response.error.data) {
			error = response.error.data as ErrorResponse;
			error = errorParser(error);
			response.error.data = error;
		}
		return response;
	};
};

const tags = [
	'User',
	'MusicJob',
	'YoutubeAuth',
	'YoutubeVideo',
	'YoutubeVideoCategory',
	'YoutubeVideoQueue',
	'YoutubeSubscription',
	'MusicGrouping',
	'MusicArtwork',
	'MusicTags',
];

const api = createApi({
	baseQuery: customBaseQuery({ baseUrl: '/api' }),
	tagTypes: tags,
	endpoints: (build) => ({
		checkSession: build.query<User, void>({
			query: () => ({
				url: '/auth/session',
			}),
			providesTags: ['User'],
		}),
		loginOrCreate: build.mutation<User | undefined, { email: string; password: string; login: boolean }>({
			query: ({ email, password, login }) => ({
				url: `/auth/${login ? 'login' : 'create'}`,
				method: 'POST',
				body: { email, password },
			}),
			invalidatesTags: (result, error, args) => (args.login && !error ? tags : []),
		}),
		logout: build.mutation<undefined, void>({
			query: () => ({
				url: '/auth/logout',
			}),
			invalidatesTags: (result, error) => (!error ? tags : []),
		}),
	}),
});

export default api;
export const { useCheckSessionQuery, useLoginOrCreateMutation, useLogoutMutation } = api;
