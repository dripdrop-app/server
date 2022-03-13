import { useEffect, useMemo } from 'react';
import { useAtomValue } from 'jotai';
import { Button, Container, Grid, Header, Loader } from 'semantic-ui-react';
import useLazyFetch from '../hooks/useLazyFetch';
import VideosView from '../components/YoutubeCollections/VideosView';
import SubscriptionsView from '../components/YoutubeCollections/SubscriptionsView';
import { authAtomState } from '../state/YoutubeCollections';

interface YoutubeCollectionsProps {
	page: 'VIDEOS' | 'SUBSCRIPTIONS';
}

const YoutubeCollections = (props: YoutubeCollectionsProps) => {
	const youtubeAuth = useAtomValue(authAtomState);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch<string>();

	useEffect(() => {
		if (getOAuthLinkStatus.success) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	const Content = useMemo(() => {
		if (youtubeAuth.loading) {
			return (
				<Container style={{ display: 'flex', alignItems: 'center' }}>
					<Loader size="huge" active />
				</Container>
			);
		}
		if (youtubeAuth.data.email) {
			return (
				<Container>
					<Grid divided="vertically">
						<Grid.Row>
							<Grid.Column>
								<Header>
									{props.page.charAt(0).toLocaleUpperCase() + props.page.substring(1).toLocaleLowerCase()}
								</Header>
							</Grid.Column>
						</Grid.Row>
						<Grid.Row>
							<Grid.Column>
								{props.page === 'VIDEOS' ? <VideosView /> : null}
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
								{youtubeAuth.data.refresh ? 'Reconnect Google Account' : 'Log in with Google'}
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		);
	}, [
		youtubeAuth.loading,
		youtubeAuth.data.email,
		youtubeAuth.data.refresh,
		getOAuthLinkStatus.loading,
		props.page,
		getOAuthLink,
	]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable padded>
					<Grid.Row>
						<Grid.Column>
							<Header as="h1">Youtube Collections</Header>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>{Content}</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[Content]
	);
};

export default YoutubeCollections;
