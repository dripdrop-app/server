import api, { tags } from '.';

const authApi = api.injectEndpoints({
	endpoints: (build) => ({
		checkSession: build.query<User, void>({
			query: () => ({
				url: '/auth/session',
			}),
			providesTags: ['User'],
		}),
		create: build.mutation<undefined, LoginBody>({
			query: ({ email, password }) => ({
				url: '/auth/create',
				method: 'POST',
				body: { email, password },
			}),
		}),
		login: build.mutation<User, LoginBody>({
			query: ({ email, password }) => ({
				url: '/auth/login',
				method: 'POST',
				body: { email, password },
			}),
			invalidatesTags: (result, error, args) => (!error ? tags : []),
		}),
		logout: build.mutation<undefined, void>({
			query: () => ({
				url: '/auth/logout',
			}),
			invalidatesTags: (result, error) => (!error ? tags : []),
		}),
	}),
});

export default authApi;
export const { useCheckSessionQuery, useCreateMutation, useLoginMutation, useLogoutMutation } = authApi;
