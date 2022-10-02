import api, { tags } from '.';

const authApi = api.injectEndpoints({
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

export default authApi;
export const { useCheckSessionQuery, useLoginOrCreateMutation, useLogoutMutation } = authApi;
