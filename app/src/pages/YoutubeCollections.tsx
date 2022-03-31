import { useEffect, useMemo } from 'react';
import { Button, Container, Grid, Header, Loader } from 'semantic-ui-react';
import { useCheckYoutubeAuthQuery, useLazyGetOauthLinkQuery } from '../api';

interface YoutubeCollectionsProps {
	title: string;
	children: JSX.Element;
}

const YoutubeCollections = (props: YoutubeCollectionsProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery(null);
	const [getOAuthLink, getOAuthLinkStatus] = useLazyGetOauthLinkQuery();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	const Content = useMemo(() => {
		if (youtubeAuthStatus.isFetching) {
			return (
				<Container style={{ display: 'flex', alignItems: 'center' }}>
					<Loader size="huge" active />
				</Container>
			);
		} else if (youtubeAuthStatus.isSuccess && youtubeAuthStatus.data.email) {
			return (
				<Container>
					<Grid divided="vertically">
						<Grid.Row>
							<Grid.Column>
								<Header>{props.title}</Header>
							</Grid.Column>
						</Grid.Row>
						<Grid.Row>
							<Grid.Column>{props.children}</Grid.Column>
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
							<Button color="blue" loading={getOAuthLinkStatus.isFetching} onClick={() => getOAuthLink(null)}>
								{youtubeAuthStatus.isSuccess && youtubeAuthStatus.data.refresh
									? 'Reconnect Google Account'
									: 'Log in with Google'}
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		);
	}, [
		youtubeAuthStatus.isFetching,
		youtubeAuthStatus.isSuccess,
		youtubeAuthStatus.data,
		getOAuthLinkStatus.isFetching,
		props.title,
		props.children,
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
