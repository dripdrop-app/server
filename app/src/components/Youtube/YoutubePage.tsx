import { useMemo } from 'react';
import { Stack, CircularProgress, Button } from '@mui/material';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../../api';
import YoutubeWrapper from './YoutubeWrapper';

interface YoutubePageProps {
	render: (user: YoutubeAuthState) => JSX.Element;
}

const YoutubePage = (props: YoutubePageProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery();
	const [getOAuthLink, getOAuthLinkStatus] = useLazyGetOauthLinkQuery();

	return useMemo(() => {
		if (youtubeAuthStatus.isFetching) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		}
		const buttonText =
			youtubeAuthStatus.isSuccess && youtubeAuthStatus.currentData && youtubeAuthStatus.currentData.refresh
				? 'Reconnect Google Account'
				: 'Log in with Google';
		return (
			<YoutubeWrapper
				render={props.render}
				altRender={
					<Stack padding={10} direction="row" justifyContent="center">
						<Button variant="contained" onClick={() => getOAuthLink()}>
							{getOAuthLinkStatus.isFetching ? <CircularProgress /> : buttonText}
						</Button>
					</Stack>
				}
			/>
		);
	}, [
		getOAuthLink,
		getOAuthLinkStatus.isFetching,
		props.render,
		youtubeAuthStatus.currentData,
		youtubeAuthStatus.isFetching,
		youtubeAuthStatus.isSuccess,
	]);
};

export default YoutubePage;
