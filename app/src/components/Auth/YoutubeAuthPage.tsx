import { useMemo, useEffect, ComponentProps } from 'react';
import { CircularProgress, Stack } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../../api/youtube';
import AuthPage from './AuthPage';

interface YoutubeAuthWrapperProps extends ComponentProps<'div'> {
	unAuthenticatedRender: () => JSX.Element;
}

export const YoutubeAuthWrapper = (props: YoutubeAuthWrapperProps) => {
	const { children, unAuthenticatedRender } = props;

	const youtubeAuthStatus = useCheckYoutubeAuthQuery();

	return useMemo(() => {
		if (youtubeAuthStatus.isFetching) {
			return (
				<Stack direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (
			youtubeAuthStatus.isSuccess &&
			youtubeAuthStatus.currentData &&
			youtubeAuthStatus.currentData.email &&
			!youtubeAuthStatus.currentData.refresh
		) {
			return <div>{children}</div>;
		}
		return unAuthenticatedRender();
	}, [
		children,
		unAuthenticatedRender,
		youtubeAuthStatus.currentData,
		youtubeAuthStatus.isFetching,
		youtubeAuthStatus.isSuccess,
	]);
};

interface YoutubeAuthPageProps extends ComponentProps<'div'> {
	children: JSX.Element;
}

const YoutubeAuthPage = (props: YoutubeAuthPageProps) => {
	const { children } = props;

	const youtubeAuthStatus = useCheckYoutubeAuthQuery();
	const [getOAuthLink, getOAuthLinkStatus] = useLazyGetOauthLinkQuery();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess && getOAuthLinkStatus.currentData) {
			const oAuthURL = getOAuthLinkStatus.currentData;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	return useMemo(() => {
		const buttonText =
			youtubeAuthStatus.isSuccess && youtubeAuthStatus.currentData && youtubeAuthStatus.currentData.refresh
				? 'Reconnect Google Account'
				: 'Log in with Google';
		return (
			<AuthPage>
				<YoutubeAuthWrapper
					unAuthenticatedRender={() => (
						<Stack direction="row" justifyContent="center">
							<LoadingButton
								variant="contained"
								loading={getOAuthLinkStatus.isFetching || getOAuthLinkStatus.isLoading}
								onClick={() => getOAuthLink()}
							>
								{buttonText}
							</LoadingButton>
						</Stack>
					)}
				>
					{children}
				</YoutubeAuthWrapper>
			</AuthPage>
		);
	}, [
		youtubeAuthStatus.isSuccess,
		youtubeAuthStatus.currentData,
		children,
		getOAuthLinkStatus.isFetching,
		getOAuthLinkStatus.isLoading,
		getOAuthLink,
	]);
};

export default YoutubeAuthPage;
