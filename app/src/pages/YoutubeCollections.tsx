import { useEffect, useMemo } from 'react';
import { useRecoilValueLoadable } from 'recoil';
import { Button, Container, Grid, Header } from 'semantic-ui-react';
import useLazyFetch from '../hooks/useLazyFetch';
import VideosView from '../components/YoutubeCollections/VideosView';
import SubscriptionsView from '../components/YoutubeCollections/SubscriptionsView';
import { authSelector } from '../state/YoutubeCollections';

interface YoutubeCollectionsProps {
	page: 'VIDEOS' | 'SUBSCRIPTIONS';
}

const YoutubeCollections = (props: YoutubeCollectionsProps) => {
	const youtubeAuth = useRecoilValueLoadable(authSelector);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch<string>();

	useEffect(() => {
		if (getOAuthLinkStatus.success) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	const Content = useMemo(() => {
		if (youtubeAuth.state === 'hasValue') {
			if (youtubeAuth.contents.email) {
				return (
					<Container>
						<Grid container divided="vertically">
							<Grid.Row>
								<Grid.Column>
									<Header>
										{props.page.charAt(0).toLocaleUpperCase() + props.page.substring(1).toLocaleLowerCase()}
									</Header>
								</Grid.Column>
							</Grid.Row>
							<Grid.Row>
								<Grid.Column>
									{props.page === 'VIDEOS' ? <VideosView channelID={null} /> : null}
									{props.page === 'SUBSCRIPTIONS' ? <SubscriptionsView /> : null}
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Container>
				);
			}
			return (
				<Container>
					<Grid>
						<Grid.Row>
							<Grid.Column textAlign="center">
								<Button
									color="blue"
									loading={getOAuthLinkStatus.loading}
									onClick={() => getOAuthLink({ url: '/youtube/oauth' })}
								>
									{youtubeAuth.contents.refresh ? 'Reconnect Google Account' : 'Log in with Google'}
								</Button>
							</Grid.Column>
						</Grid.Row>
					</Grid>
				</Container>
			);
		}
	}, [
		props.page,
		getOAuthLink,
		getOAuthLinkStatus.loading,
		youtubeAuth.contents.email,
		youtubeAuth.contents.refresh,
		youtubeAuth.state,
	]);

	return useMemo(
		() => (
			<Container>
				<Grid container padded>
					<Grid.Row>
						<Grid.Column>
							<Header as="h1">Youtube Collections</Header>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>{Content}</Grid.Row>
				</Grid>
			</Container>
		),
		[Content]
	);
};

export default YoutubeCollections;
