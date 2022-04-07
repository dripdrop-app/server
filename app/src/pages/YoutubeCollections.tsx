import { useEffect, useMemo } from 'react';
import { CircularProgress, Container, Stack, Typography, Button } from '@mui/material';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../api';

interface YoutubeCollectionsProps {
	title: string;
	children: JSX.Element;
}

const YoutubeCollections = (props: YoutubeCollectionsProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery(null);
	const [getOAuthLink, getOAuthLinkStatus] = useLazyGetOauthLinkQuery();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess && getOAuthLinkStatus.currentData) {
			const oAuthURL = getOAuthLinkStatus.currentData;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	const Content = useMemo(() => {
		if (youtubeAuthStatus.isFetching) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (youtubeAuthStatus.isSuccess && youtubeAuthStatus.currentData.email) {
			return (
				<Stack paddingY={2}>
					<Typography variant="h6">{props.title}</Typography>
					{props.children}
				</Stack>
			);
		}
		const buttonText =
			youtubeAuthStatus.isSuccess && youtubeAuthStatus.currentData.refresh
				? 'Reconnect Google Account'
				: 'Log in with Google';
		return (
			<Stack padding={10} direction="row" justifyContent="center">
				<Button variant="contained" onClick={() => getOAuthLink(null)}>
					{getOAuthLinkStatus.isFetching ? <CircularProgress /> : buttonText}
				</Button>
			</Stack>
		);
	}, [
		youtubeAuthStatus.isFetching,
		youtubeAuthStatus.isSuccess,
		youtubeAuthStatus.currentData,
		getOAuthLinkStatus.isFetching,
		props.title,
		props.children,
		getOAuthLink,
	]);

	return useMemo(
		() => (
			<Container>
				<Stack paddingY={2}>
					<Typography variant="h3">Youtube Collections</Typography>
					{Content}
				</Stack>
			</Container>
		),
		[Content]
	);
};

export default YoutubeCollections;
