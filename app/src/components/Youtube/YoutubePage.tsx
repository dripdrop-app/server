import { useMemo } from 'react';
import { Stack, CircularProgress, Button } from '@mui/material';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../../api';
import YoutubeWrapper from './YoutubeWrapper';
import ConditionalDisplay from '../ConditionalDisplay';

interface YoutubePageProps {
	render: (user: YoutubeAuthState) => JSX.Element;
}

const YoutubePage = (props: YoutubePageProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery();
	const [getOAuthLink, getOAuthLinkStatus] = useLazyGetOauthLinkQuery();

	return useMemo(() => {
		const buttonText =
			youtubeAuthStatus.isSuccess && youtubeAuthStatus.currentData && youtubeAuthStatus.currentData.refresh
				? 'Reconnect Google Account'
				: 'Log in with Google';
		return (
			<YoutubeWrapper
				showLoading={true}
				render={props.render}
				altRender={
					<Stack padding={10} direction="row" justifyContent="center">
						<Button variant="contained" onClick={() => getOAuthLink()}>
							<ConditionalDisplay condition={getOAuthLinkStatus.isFetching}>
								<CircularProgress />
							</ConditionalDisplay>
							<ConditionalDisplay condition={!getOAuthLinkStatus.isFetching}>{buttonText}</ConditionalDisplay>
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
		youtubeAuthStatus.isSuccess,
	]);
};

export default YoutubePage;
