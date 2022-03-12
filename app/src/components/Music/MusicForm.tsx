import React, { useMemo, useRef } from 'react';
import { Container, Grid, Header } from 'semantic-ui-react';
import ArtworkInput from './ArtworkInput';
import SourceSelector from './SourceSelector';
import FormActions from './FormActions';
import TagInputs from './TagInputs';

const MusicForm = () => {
	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	return useMemo(
		() => (
			<Container>
				<Grid stackable padded="vertically">
					<Grid.Row>
						<Grid.Column>
							<Header as="h1">MP3 Downloader / Converter</Header>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<SourceSelector fileInputRef={fileInputRef} />
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<ArtworkInput />
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<TagInputs />
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<FormActions fileInputRef={fileInputRef} />
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[]
	);
};

export default MusicForm;
