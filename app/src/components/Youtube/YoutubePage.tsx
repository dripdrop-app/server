import { useMemo, useEffect } from 'react';
import { Stack, CircularProgress, Button } from '@mui/material';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../../api/youtube';
import YoutubeWrapper from './YoutubeWrapper';
import ConditionalDisplay from '../ConditionalDisplay';

interface YoutubePageProps {
	children: JSX.Element;
}

const YoutubePage = (props: YoutubePageProps) => {
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
			<YoutubeWrapper
				showLoading={true}
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
			>
				{props.children}
			</YoutubeWrapper>
		);
	}, [
		getOAuthLink,
		getOAuthLinkStatus.isFetching,
		props.children,
		youtubeAuthStatus.currentData,
		youtubeAuthStatus.isSuccess,
	]);
};

export default YoutubePage;
